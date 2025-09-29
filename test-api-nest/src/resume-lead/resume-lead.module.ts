import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { ResumeLeadController } from './resume-lead.controller';
import { ResumeLeadService } from './resume-lead.service';
import { ResumeLead, ResumeLeadSchema } from './schemas/resume-lead.schema';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: ResumeLead.name, schema: ResumeLeadSchema },
    ]),
  ],
  controllers: [ResumeLeadController],
  providers: [ResumeLeadService],
  exports: [ResumeLeadService],
})
export class ResumeLeadModule {}