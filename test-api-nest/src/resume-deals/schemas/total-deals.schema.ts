import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { Document } from 'mongoose';

export type TotalDealsDocument = TotalDeals & Document;

@Schema({ collection: 'total_deals' })
export class TotalDeals {
  @Prop({ required: true })
  id: string;

  @Prop({ required: true })
  amount: number;

  @Prop({ required: true })
  total: number;
}

export const TotalDealsSchema = SchemaFactory.createForClass(TotalDeals);