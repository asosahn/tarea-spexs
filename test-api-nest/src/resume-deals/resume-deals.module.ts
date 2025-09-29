import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { ResumeDealsController } from './resume-deals.controller';
import { ResumeDealsService } from './resume-deals.service';
import { TotalDeals, TotalDealsSchema } from './schemas/total-deals.schema';
import {
  ResumeCloseDeals,
  ResumeCloseDealsSchema,
} from './schemas/resume-close-deals.schema';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: TotalDeals.name, schema: TotalDealsSchema },
      { name: ResumeCloseDeals.name, schema: ResumeCloseDealsSchema },
    ]),
  ],
  controllers: [ResumeDealsController],
  providers: [ResumeDealsService],
})
export class ResumeDealsModule {}
